! Description:
! Definition of an element surface.
module m_surface
    implicit none
    
    private
    public t_surface, new_surface
    
    type t_surface
        integer              :: n_nodes    ! number of element nodes
        integer              :: i_element  ! index of element
        integer, allocatable :: i_nodes(:) ! index of element nodes
    contains
        final :: destructor
    end type
    
    interface new_surface
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Surface constructor.
    type(t_surface) function constructor(i_element, n_nodes) result(self)
        integer, intent(in) :: n_nodes   ! number of element nodes
        integer, intent(in) :: i_element ! index of element
        self%n_nodes   = n_nodes
        self%i_element = i_element
        allocate(self%i_nodes(self%n_nodes))
    end function
    
    ! Description:
    ! Surface destructor.
    subroutine destructor(self)
        type(t_surface), intent(inout) :: self
        if (allocated(self%i_nodes)) deallocate(self%i_nodes)
    end subroutine
    
end module
